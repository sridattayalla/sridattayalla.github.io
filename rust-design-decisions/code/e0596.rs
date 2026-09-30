fn main() {
    let s = String::from("hello");
    let r = &s;
    r.push_str("world");
    println!("{r}");
}
