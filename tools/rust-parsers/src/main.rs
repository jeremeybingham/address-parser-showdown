//! Worker for the three Rust-only parsers, driven from Python like `adapters/libpostal_worker.py`.
//!
//! Usage: `rust-parsers --parser {address_parser,addrust,us_address_parser}`
//! In  (one JSON line per request): {"strings": ["..."]}
//! Out (one JSON line per request): {"results": [{"fields": [[label, value], ...]} | {"error": "..."}, ...]}
//! A parse that panics or finds nothing usable is an error for that string only.

use std::io::{BufRead, Write};
use std::panic::{catch_unwind, AssertUnwindSafe};

use serde_json::{json, Value};

type Fields = Vec<(String, String)>;

fn address_parser(s: &str) -> Result<Fields, String> {
    let a = address_parser::parse_address(s).ok_or("no parse")?;
    Ok(a.iter().map(|(c, v)| (c.name().to_string(), v.to_string())).collect())
}

fn us_address_parser(s: &str) -> Result<Fields, String> {
    let a = us_address_parser::string_to_address(&s.to_string());
    let pairs = [
        ("street_no", a.street_no),
        ("direction", a.direction),
        ("street_name", a.street_name),
        ("street_type", a.street_type),
        ("unit_type", a.unit_type),
        ("unit_no", a.unit_no),
    ];
    Ok(pairs.into_iter().filter_map(|(k, v)| v.map(|v| (k.to_string(), v))).collect())
}

fn addrust(s: &str) -> Result<Fields, String> {
    // Shipped defaults: Pipeline::default(), no config file read. Built once: `addrust::parse` rebuilds it (compiles
    // every pattern) on each call, which made it about 500 times slower.
    thread_local! {
        static PIPELINE: ::addrust::pipeline::Pipeline = ::addrust::pipeline::Pipeline::default();
    }
    let a = PIPELINE.with(|p| p.parse(s));
    Ok(::addrust::address::COL_DEFS
        .iter()
        .filter_map(|d| a.field(d.col).clone().map(|v| (d.key.to_string(), v)))
        .collect())
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let name = match args.iter().position(|a| a == "--parser").and_then(|i| args.get(i + 1)) {
        Some(n) => n.as_str(),
        None => {
            eprintln!("usage: rust-parsers --parser {{address_parser,addrust,us_address_parser}}");
            std::process::exit(2);
        }
    };
    let parse: fn(&str) -> Result<Fields, String> = match name {
        "address_parser" => address_parser,
        "addrust" => addrust,
        "us_address_parser" => us_address_parser,
        other => {
            eprintln!("unknown parser: {other}");
            std::process::exit(2);
        }
    };
    std::panic::set_hook(Box::new(|_| {})); // a panic is reported per string, not on stderr
    let stdout = std::io::stdout();
    for line in std::io::stdin().lock().lines() {
        let line = line.expect("stdin");
        let results: Vec<Value> = match serde_json::from_str::<Value>(&line) {
            Ok(req) => req["strings"]
                .as_array()
                .map(|v| v.as_slice())
                .unwrap_or_default()
                .iter()
                .map(|s| {
                    let s = s.as_str().unwrap_or("");
                    match catch_unwind(AssertUnwindSafe(|| parse(s))) {
                        Ok(Ok(f)) => json!({ "fields": f }),
                        Ok(Err(e)) => json!({ "error": e }),
                        Err(_) => json!({ "error": "panic" }),
                    }
                })
                .collect(),
            Err(e) => {
                vec![json!({ "error": format!("bad request: {e}") })]
            }
        };
        let mut out = stdout.lock();
        writeln!(out, "{}", json!({ "results": results })).expect("stdout");
        out.flush().expect("flush");
    }
}
