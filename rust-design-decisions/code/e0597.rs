fn main() {
    let r;
    {
        let s = String::from("hello");
        r = &s;
    }
    println!("{r}");
}
