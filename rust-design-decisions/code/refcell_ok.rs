use std::cell::RefCell;

fn main() {
    let cell = RefCell::new(vec![1, 2, 3]);
    cell.borrow_mut().push(4);
    println!("len: {}", cell.borrow().len());
}
