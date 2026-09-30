enum List {
    Cons(i32, Box<List>),
    Nil,
}

fn main() {
    let l = List::Cons(1, Box::new(List::Cons(2, Box::new(List::Nil))));
    match l {
        List::Cons(head, rest) => {
            println!("head {head}");
            match *rest {
                List::Cons(h, _) => println!("tail head {h}"),
                List::Nil => println!("tail empty"),
            }
        }
        List::Nil => println!("empty"),
    }
}
