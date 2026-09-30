fn main() {
    let mut s = String::from("hello");
    let r = &s;
    s = String::from("world");
    println!("{r}");
}
