use std::cell::Cell;

fn main() {
    let c = Cell::new(41);
    let shared = &c;
    shared.set(shared.get() + 1);
    println!("value: {}", c.get());
}
