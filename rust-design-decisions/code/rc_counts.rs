use std::rc::Rc;

fn main() {
    let a = Rc::new(String::from("shared"));
    let b = Rc::clone(&a);
    let c = Rc::clone(&a);
    println!("count after 3 handles: {}", Rc::strong_count(&a));
    drop(b);
    println!("count after dropping b: {}", Rc::strong_count(&a));
    println!("data via c: {}", c);
}
