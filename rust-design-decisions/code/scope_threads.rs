use std::thread;

fn main() {
    let data = vec![10, 20, 30];
    thread::scope(|s| {
        let a = s.spawn(|| data.iter().sum::<i32>());
        let b = s.spawn(|| data.len());
        println!("sum: {}, len: {}", a.join().unwrap(), b.join().unwrap());
    });
}
