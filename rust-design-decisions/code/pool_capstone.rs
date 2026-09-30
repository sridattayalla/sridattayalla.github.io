use std::sync::{mpsc, Arc, Mutex};
use std::thread;
type Job = Box<dyn FnOnce() + Send + 'static>;

fn main() {
    let (tx, rx) = mpsc::channel::<Job>();
    let rx = Arc::new(Mutex::new(rx));
    let mut workers = vec![];
    for id in 0..3 {
        let rx = Arc::clone(&rx);
        workers.push(thread::spawn(move || {
            loop {
                let message = rx.lock().unwrap().recv();
                match message {
                    Ok(job) => { println!("worker {} picked up a job", id); job(); }
                    Err(_) => break,
                }
            }
        }));
    }
    for i in 0..5 {
        tx.send(Box::new(move || println!("job {} done", i))).unwrap();
    }
    drop(tx);
    for w in workers {
        w.join().unwrap();
    }
    println!("pool shut down cleanly");
}
