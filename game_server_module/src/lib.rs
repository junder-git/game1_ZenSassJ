use spacetimedb::{table, reducer, ReducerContext, Table};

#[table(name = person, public)]
pub struct Person {
    name: String,
}

#[reducer]
pub fn add(ctx: &ReducerContext, name: String) {
    log::info!("Inserting {}", name);
    ctx.db.person().insert(Person { name });
}

#[reducer]
pub fn say_hello(ctx: &ReducerContext) {
    for person in ctx.db.person().iter() {
        log::info!("Hello, {}!", person.name);
    }
    log::info!("Hello, World!");
}
