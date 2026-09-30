struct Field(&'static str);
impl Drop for Field {
    fn drop(&mut self) { println!("drop {}", self.0); }
}
fn main() {
    let mut held = Field("first");
    println!("holding {}", held.0);
    held = Field("second");
    println!("holding {}", held.0);
}
