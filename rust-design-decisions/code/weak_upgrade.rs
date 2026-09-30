use std::rc::{Rc, Weak};

fn main() {
    let a = Rc::new(String::from("payload"));
    let weak: Weak<String> = Rc::downgrade(&a);
    println!("while alive: {:?}", weak.upgrade());
    drop(a);
    println!("after drop: {:?}", weak.upgrade());
}
