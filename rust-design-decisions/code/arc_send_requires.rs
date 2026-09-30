use std::cell::Cell;
use std::sync::Arc;
use std::thread;

fn main() {
    let counter = Arc::new(Cell::new(0u32));
    let handle = thread::spawn(move || {
        counter.set(counter.get() + 1);
    });
    handle.join().unwrap();
    println!("count: {}", counter.get());
}
