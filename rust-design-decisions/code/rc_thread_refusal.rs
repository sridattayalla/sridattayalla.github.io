use std::rc::Rc;
use std::thread;

fn main() {
    let a = Rc::new(String::from("hello"));
    let handle = thread::spawn(move || {
        println!("{a}");
    });
    handle.join().unwrap();
}
