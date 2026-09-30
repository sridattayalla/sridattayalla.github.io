enum List { Cons(i32, List), Nil }

fn main() {
    let l = List::Cons(1, List::Cons(2, List::Nil));
    match l {
        List::Cons(head, _) => println!("head {head}"),
        List::Nil => println!("empty"),
    }
}
