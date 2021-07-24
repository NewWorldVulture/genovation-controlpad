// Created by Ada (NewWorldVulture)

extern crate hidapi;
use std::io;
use std::io::prelude::*;
use std::fs::File;
use std::env;

fn main() -> io::Result<()> {
    // Collect file to read
    let args: Vec<String> = env::args().collect();
    let filename: &String = &args[1];
    let mut f = File::open(filename)?;

    // Read contents of file into buffer
    let mut buffer = Vec::new();
    f.read_to_end(&mut buffer)?;

    let api = hidapi::HidApi::new().unwrap();
    // Select GENOVATION Keypad by VID, PID
    let (vid, pid) = (0x1125, 0x1807);
    let device = api.open(vid, pid).unwrap();

    for byte in &buffer {
        let sm_buff = [0u8, 1u8, *byte, 0u8, 0u8, 0u8];
        let result = device.send_feature_report(&sm_buff);

        match result {
            Ok(bytes) => { println!("Wrote: {:?} bytes", bytes) },
            Err(e) => { eprintln!("{:?}", e) },
    }
    }


    Ok(())
}
