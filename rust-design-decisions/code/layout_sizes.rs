use std::mem::size_of;

fn main() {
    println!("&str       {} bytes", size_of::<&str>());
    println!("String     {} bytes", size_of::<String>());
    println!("&[u32]     {} bytes", size_of::<&[u32]>());
    println!("Vec<u32>   {} bytes", size_of::<Vec<u32>>());
    println!("Box<u32>   {} bytes", size_of::<Box<u32>>());
    println!("&u32       {} bytes", size_of::<&u32>());
}
