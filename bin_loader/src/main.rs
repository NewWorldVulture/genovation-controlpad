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

    let mut completed: bool = true;
    for byte in &buffer {
        // First byte is SET_REPORT ID. We only ever use 0x0
        let sm_buff = [0u8, 1u8, *byte, 0u8, 0u8, 0u8];
        let result = device.send_feature_report(&sm_buff);

        match result {
            Ok(_) => { },
            Err(e) => { eprintln!("{:?}", e);
                        completed = false; },
        }
    }

    if completed {
        println!("Keypad configured.");
    } else {
        println!("Keypad configuration not successful.");
    }

    Ok(())
}
