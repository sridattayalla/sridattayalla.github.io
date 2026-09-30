fn main() {
    let mut s = String::from("hello");
    let a = &mut s;
    let b = &mut s;
    a.push('!');
}
