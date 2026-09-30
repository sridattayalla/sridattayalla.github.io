use std::cell::RefCell;
use std::rc::{Rc, Weak};

struct Node {
    next: RefCell<Option<Weak<Node>>>,
}

impl Drop for Node {
    fn drop(&mut self) {
        println!("Node dropped");
    }
}

fn main() {
    let a = Rc::new(Node { next: RefCell::new(None) });
    let b = Rc::new(Node { next: RefCell::new(None) });
    *a.next.borrow_mut() = Some(Rc::downgrade(&b));
    *b.next.borrow_mut() = Some(Rc::downgrade(&a));
    println!("a strong: {}", Rc::strong_count(&a));
    println!("weak to a: {}", Rc::weak_count(&a));
}
