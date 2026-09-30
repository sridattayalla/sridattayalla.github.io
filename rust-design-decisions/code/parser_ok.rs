struct Parser<'a> {
    text: &'a str,
}

fn longest_word<'a>(a: &'a str, b: &'a str) -> &'a str {
    if a.len() >= b.len() { a } else { b }
}

fn main() {
    let p = Parser { text: "hello alpha" };
    let other = String::from("beta");
    let w = longest_word(p.text, &other);
    println!("{} {}", p.text, w);
}
