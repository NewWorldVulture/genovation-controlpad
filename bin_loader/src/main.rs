// Created by NewWorldVulture (Ada MacLurg)
// 


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
    // Select GENOVATION Keypad by VendorID (0x1125 - Genovation),
    // and Product ID (0x1807 - ControlPad CP24)
    // If I ever need to program a different product
    // ...we just need to change the values here
    let (vid, pid) = (0x1125, 0x1807);
    let device = api.open(vid, pid).unwrap();

    let mut completed: bool = true;
    for byte in &buffer {
        // 0u8 -> SET_REPORT ID. We only ever use 0x0
        // 1u8 -> Marks data as config data
        // *byte -> Byte of Data
        let sm_buff = [0u8, 1u8, *byte, 0u8, 0u8, 0u8];

        // Try to send this byte up to 5 times
        let mut tries: u8 = 0;
        let mut byte_sent: bool = false;
        while !byte_sent && tries < 5 {
            let result = device.send_feature_report(&sm_buff);

            match result {
                Ok(_)  => { byte_sent = true;
                            break; },
                Err(e) => { eprintln!("{:?}", e); },
            }
            tries += 1;
            if tries == 5 {
                completed = false;
            }
        }
    }

    if completed {
        println!("Keypad configured.");
    } else {
        println!("Keypad configuration not successful.");
    }

    Ok(())
}
