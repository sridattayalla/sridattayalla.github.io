use std::slice;

fn split_at_mut(slice: &mut [i32]) -> (&mut [i32], &mut [i32]) {
    let len = slice.len();
    let ptr = slice.as_mut_ptr();
    let mid = len / 2;
    // SAFETY: ptr is valid for len aligned i32 elements because it came
    // from this slice; the ranges [ptr, ptr+mid) and [ptr+mid, ptr+len)
    // are disjoint halves whose lengths sum to len.
    unsafe {
        assert!(mid <= len);
        (
            slice::from_raw_parts_mut(ptr, mid),
            slice::from_raw_parts_mut(ptr.add(mid), len - mid),
        )
    }
}

fn main() {
    let mut data = vec![1, 2, 3, 4, 5, 6];
    let (a, b) = split_at_mut(&mut data);
    a[0] = 100;
    b[0] = 200;
    println!("{:?}", data);
}
