fn first_word(s: &str) -> &str {
    let bytes = s.as_bytes();
    for (i, &item) in bytes.iter().enumerate() {
        if item == b' ' {
            return &s[..i];
        }
    }
    s
}

fn make(name: &str) -> &str {
    let s = String::from(name);
    &s
}

fn main() {
    let w = first_word(&String::from("hello world"));
    println!("{w}");
}
