use std::error::Error;
use std::fs;

fn read_config(path: &str) -> Result<String, Box<dyn Error>> {
    let text = fs::read_to_string(path)?;
    Ok(text)
}

fn parse_pair(a: &str, b: &str) -> Result<(i32, i32), std::num::ParseIntError> {
    let x: i32 = a.parse()?;
    let y: i32 = b.parse()?;
    Ok((x, y))
}

fn main() {
    match read_config("/does-not-exist.conf") {
        Ok(text) => println!("read {} bytes", text.len()),
        Err(e) => println!("error: {}", e),
    }
    println!("{:?}", parse_pair("3", "x"));
}
