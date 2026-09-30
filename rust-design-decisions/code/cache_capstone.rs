use std::sync::{Arc, RwLock};
use std::thread;
struct Cache { entries: Vec<String>, writes: usize }
fn main() {
    let cache = Arc::new(RwLock::new(Cache { entries: vec![], writes: 0 }));
    let mut handles = vec![];
    for t in 0..2 {
        let cache = Arc::clone(&cache);
        handles.push(thread::spawn(move || {
            for i in 0..3 {
                let mut guard = cache.write().unwrap();
                guard.entries.push(format!("w{}e{}", t, i));
                guard.writes += 1;
            }
        }));
    }
    for _ in 0..3 {
        let cache = Arc::clone(&cache);
        handles.push(thread::spawn(move || {
            for _ in 0..5 {
                drop(cache.read().unwrap());
            }
        }));
    }
    for h in handles {
        h.join().unwrap();
    }
    let guard = cache.read().unwrap();
    println!("entries: {}, writes: {}", guard.entries.len(), guard.writes);
}
