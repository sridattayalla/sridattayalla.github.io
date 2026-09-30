use std::cell::{Cell, RefCell};
use std::sync::{Arc, Mutex};

fn is_send<T: Send>() {}
fn is_sync<T: Sync>() {}

fn main() {
    is_send::<u32>();
    is_sync::<u32>();
    is_send::<Arc<Vec<u32>>>();
    is_sync::<Arc<Vec<u32>>>();
    is_send::<Cell<u32>>();
    is_send::<RefCell<u32>>();
    is_send::<Mutex<u32>>();
    is_sync::<Mutex<u32>>();
    println!("every assertion compiled: the marks are in the types");
}
