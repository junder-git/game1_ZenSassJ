use spacetimedb::{spacetimedb, println, Identity, ReducerContext, SpacetimeType, Timestamp};

// Define your data model
#[spacetimedb::table]
#[derive(Clone, Debug, PartialEq, SpacetimeType)]
pub struct GameEntity {
    #[spacetimedb::primarykey]
    pub id: u64,
    pub position_x: f32,
    pub position_y: f32,
    pub position_z: f32,
    pub owner: Identity,
    pub created_at: Timestamp,
}

// Example reducer to create a new entity
#[spacetimedb::reducer]
pub fn create_entity(ctx: ReducerContext, position_x: f32, position_y: f32, position_z: f32) -> u64 {
    let entity_id = generate_id();
    
    GameEntity::insert(GameEntity {
        id: entity_id,
        position_x,
        position_y,
        position_z,
        owner: ctx.sender,
        created_at: ctx.timestamp,
    })
    .unwrap();
    
    println!("Entity created with ID: {}", entity_id);
    entity_id
}

// Example reducer to update entity position
#[spacetimedb::reducer]
pub fn update_entity_position(
    ctx: ReducerContext,
    entity_id: u64,
    position_x: f32,
    position_y: f32,
    position_z: f32,
) -> bool {
    // Get the entity
    let entity = match GameEntity::filter_by_id(&entity_id).first() {
        Some(entity) => entity,
        None => {
            println!("Entity with ID {} not found", entity_id);
            return false;
        }
    };

    // Check if the sender is the owner
    if entity.owner != ctx.sender {
        println!("Only the owner can update this entity");
        return false;
    }

    // Update the entity
    GameEntity::update_by_id(
        &entity_id,
        GameEntity {
            id: entity_id,
            position_x,
            position_y,
            position_z,
            owner: entity.owner,
            created_at: entity.created_at,
        },
    )
    .unwrap();

    println!("Entity {} position updated", entity_id);
    true
}

// Example query to get all entities
#[spacetimedb::query]
pub fn get_all_entities() -> Vec<GameEntity> {
    GameEntity::iter().collect()
}

// Helper function to generate a unique ID
fn generate_id() -> u64 {
    use std::time::{SystemTime, UNIX_EPOCH};
    let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap();
    now.as_secs() * 1000 + now.subsec_millis() as u64
}

// Module initialization
#[spacetimedb::init]
pub fn init() {
    println!("Game server module initialized!");
}