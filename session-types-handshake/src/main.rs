use std::thread::spawn;

extern crate session_types;
use session_types::*;

// Model of an AXI-style handshake.
// This is a synchronous design and low level.
// Turns out it's not a good fit for session types.

type ReadySend = Rec<Send<bool, Var<Z>>>;
type ReadyRecv = Rec<Recv<bool, Var<Z>>>;

type ValidSend = Rec<Send<bool, Var<Z>>>;
type ValidRecv = Rec<Recv<bool, Var<Z>>>;

type DataSend = Rec<Send<u8, Var<Z>>>;
type DataRecv = Rec<Recv<u8, Var<Z>>>;


// A module which either returns the i8
// or the sign-extended value as an i16.
fn source(ready: Chan<(), ReadyRecv>, valid: Chan<(), ValidSend>, data: Chan<(), DataSend>) {
    let mut ready = ready.enter();
    let mut valid = valid.enter();
    let mut data = data.enter();

    let values_and_compute_time = [(0, 8), (1, 2), (2, 5), (3, 2)];

    for (value, compute_time) in values_and_compute_time {
        for _ in 0..compute_time {
            let (ready_inner, _) = ready.recv();
            ready = ready_inner.zero();
            valid = valid.send(false).zero();
            data = data.send(255).zero();
        }
        loop {
            let (ready_inner, ready_val) = ready.recv();
            ready = ready_inner.zero();
            valid = valid.send(true).zero();
            data = data.send(value).zero();
            if ready_val {
                break;
            }
        }
    }
    // We didn't put termination into the protocol, so we can't call close. Ow.
}


fn dest(ready: Chan<(), ReadySend>, valid: Chan<(), ValidRecv>, data: Chan<(), DataRecv>) {
    let mut ready = ready.enter();
    let mut valid = valid.enter();
    let mut data = data.enter();

    let compute_times = [1, 9, 1, 3];

    for time in compute_times {
        for _ in 0..time {
            ready = ready.send(false).zero();

            let (valid_inner, _) = valid.recv();
            valid = valid_inner.zero();

            let (data_inner, _) = data.recv();
            data = data_inner.zero();

            println!("Busy...");
        }

        loop {
            ready = ready.send(true).zero();

            let (valid_inner, valid_value) = valid.recv();
            valid = valid_inner.zero();

            let (data_inner, data_value) = data.recv();
            data = data_inner.zero();

            if valid_value {
                println!("Received new data: {data_value}");
                break;
            } else {
                println!("Waiting...");
            }
        }
    }
    // We didn't put termination into the protocol, so we can't call close. Ow.
}

fn main() {
    let (ready_send, ready_recv) = session_channel();
    let (valid_send, valid_recv) = session_channel();
    let (data_send, data_recv) = session_channel();

    let t = spawn(move || source(ready_recv, valid_send, data_send));
    dest(ready_send, valid_recv, data_recv);
    t.join().unwrap();
}
