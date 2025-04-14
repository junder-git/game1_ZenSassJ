import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { SpacetimeDBClient, Identity } from '@clockworklabs/spacetimedb-sdk';

// SpacetimeDB connection configuration
const SPACETIME_HOST = process.env.SPACETIME_HOST || 'localhost';
const SPACETIME_PORT = process.env.SPACETIME_PORT || '4000';
const MODULE_NAME = 'spacetime-game-server';

// Game entity type definition (should match server definition)
interface GameEntity {
    id: bigint;
    position_x: number;
    position_y: number;
    position_z: number;
    owner: Identity;
    created_at: bigint;
}

// Three.js scene setup
let scene: THREE.Scene;
let camera: THREE.PerspectiveCamera;
let renderer: THREE.WebGLRenderer;
let controls: OrbitControls;

// Entity tracking
const entities = new Map<string, THREE.Mesh>();

// Initialize the 3D scene
function initScene() {
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x222222);

    // Camera setup
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(5, 5, 5);
    camera.lookAt(0, 0, 0);

    // Renderer setup
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    // Controls
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;

    // Lighting
    const ambientLight = new THREE.AmbientLight(0x404040);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(1, 1, 1).normalize();
    scene.add(directionalLight);

    // Grid helper
    const gridHelper = new THREE.GridHelper(10, 10);
    scene.add(gridHelper);

    // Handle window resize
    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });

    // Animation loop
    function animate() {
        requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
    }
    animate();
}

// Create entity in 3D scene
function createEntityObject(entity: GameEntity) {
    const geometry = new THREE.BoxGeometry(0.5, 0.5, 0.5);
    const material = new THREE.MeshLambertMaterial({ color: 0x00ff00 });
    const mesh = new THREE.Mesh(geometry, material);
    
    mesh.position.set(entity.position_x, entity.position_y, entity.position_z);
    scene.add(mesh);
    
    return mesh;
}

// Update entity position in 3D scene
function updateEntityPosition(mesh: THREE.Mesh, entity: GameEntity) {
    mesh.position.set(entity.position_x, entity.position_y, entity.position_z);
}

// Connect to SpacetimeDB
async function connectToSpacetimeDB() {
    try {
        const client = new SpacetimeDBClient();
        
        // Connect to the module
        console.log(`Connecting to SpacetimeDB at ${SPACETIME_HOST}:${SPACETIME_PORT}`);
        await client.connect(`ws://${SPACETIME_HOST}:${SPACETIME_PORT}`, MODULE_NAME);
        console.log('Connected to SpacetimeDB');

        // Subscribe to entity updates
        client.subscribe<GameEntity>('GameEntity', (entity, operation) => {
            const entityId = entity.id.toString();
            
            if (operation === 'insert' || operation === 'update') {
                // Create or update the entity in the scene
                if (entities.has(entityId)) {
                    updateEntityPosition(entities.get(entityId)!, entity);
                } else {
                    const mesh = createEntityObject(entity);
                    entities.set(entityId, mesh);
                }
            } else if (operation === 'delete') {
                // Remove the entity from the scene
                if (entities.has(entityId)) {
                    scene.remove(entities.get(entityId)!);
                    entities.delete(entityId);
                }
            }
        });

        // Get all existing entities
        const existingEntities = await client.query<GameEntity>('get_all_entities', []);
        existingEntities.forEach(entity => {
            const mesh = createEntityObject(entity);
            entities.set(entity.id.toString(), mesh);
        });

        // Example: Create a new entity when clicking in the scene
        document.addEventListener('keydown', (event) => {
            if (event.key === 'c') {
                const x = Math.random() * 10 - 5;
                const y = Math.random() * 2;
                const z = Math.random() * 10 - 5;
                
                client.reducer<number>('create_entity', [x, y, z])
                    .then(entityId => console.log(`Created entity with ID: ${entityId}`))
                    .catch(err => console.error('Error creating entity:', err));
            }
        });

    } catch (error) {
        console.error('Error connecting to SpacetimeDB:', error);
    }
}

// Initialize everything
async function init() {
    initScene();
    await connectToSpacetimeDB();
    
    console.log('Press "c" to create a new entity');
}

init();