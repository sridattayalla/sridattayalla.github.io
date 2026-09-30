struct Parser {
    text: &str,
}
fn main() {
    let p = Parser { text: "hi there" };
    println!("{}", p.text);
}
