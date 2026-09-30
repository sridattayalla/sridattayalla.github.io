use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    let shared = Arc::new(Mutex::new(vec![1, 2, 3]));
    let worker = Arc::clone(&shared);
    let handle = thread::spawn(move || {
        let mut data = worker.lock().unwrap();
        data.push(4);
        panic!("worker failed mid-hold");
    });
    assert!(handle.join().is_err());
    let attempt = shared.lock();
    match attempt {
        Ok(_) => println!("lock clean"),
        Err(poisoned) => {
            let data = poisoned.into_inner();
            println!("recovered {:?}", data);
        }
    }
}
