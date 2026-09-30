use std::cell::RefCell;

fn main() {
    let cell = RefCell::new(vec![1, 2, 3]);
    let r = cell.borrow();
    cell.borrow_mut().push(4);
    println!("{} {:?}", r.len(), r);
}
