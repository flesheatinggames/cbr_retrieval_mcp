
RUST_BUFFERS_CASES = [
    
    # ============================================
    # BYTES AND BUFFER HANDLING
    # ============================================
    {
        "problem": "Efficient binary data handling using bytes crate with zero-copy operations.",
        "solution": """
use bytes::{Bytes, BytesMut, Buf, BufMut};
use std::io::{self, Read, Write};

// Binary protocol parser
#[derive(Debug, Clone)]
pub struct MessageHeader {
    pub magic: u32,
    pub version: u8,
    pub message_type: u8,
    pub payload_length: u32,
}

impl MessageHeader {
    const SIZE: usize = 10; // 4 + 1 + 1 + 4

    pub fn new(message_type: u8, payload_length: u32) -> Self {
        Self {
            magic: 0xDEADBEEF,
            version: 1,
            message_type,
            payload_length,
        }
    }

    pub fn encode(&self, buf: &mut BytesMut) {
        buf.put_u32_le(self.magic);
        buf.put_u8(self.version);
        buf.put_u8(self.message_type);
        buf.put_u32_le(self.payload_length);
    }

    pub fn decode(buf: &mut impl Buf) -> Result<Self, &'static str> {
        if buf.remaining() < Self::SIZE {
            return Err("Insufficient bytes for header");
        }

        let magic = buf.get_u32_le();
        if magic != 0xDEADBEEF {
            return Err("Invalid magic number");
        }

        let version = buf.get_u8();
        let message_type = buf.get_u8();
        let payload_length = buf.get_u32_le();

        Ok(Self {
            magic,
            version,
            message_type,
            payload_length,
        })
    }
}

#[derive(Debug, Clone)]
pub struct Message {
    pub header: MessageHeader,
    pub payload: Bytes,
}

impl Message {
    pub fn new(message_type: u8, payload: Bytes) -> Self {
        let header = MessageHeader::new(message_type, payload.len() as u32);
        Self { header, payload }
    }

    pub fn encode(&self) -> BytesMut {
        let total_size = MessageHeader::SIZE + self.payload.len();
        let mut buf = BytesMut::with_capacity(total_size);
        
        self.header.encode(&mut buf);
        buf.put_slice(&self.payload);
        
        buf
    }

    pub fn decode(buf: &mut impl Buf) -> Result<Self, &'static str> {
        let header = MessageHeader::decode(buf)?;
        
        if buf.remaining() < header.payload_length as usize {
            return Err("Insufficient bytes for payload");
        }

        let payload = buf.copy_to_bytes(header.payload_length as usize);
        
        Ok(Self { header, payload })
    }
}

// Chunked data processor
pub struct ChunkedProcessor {
    buffer: BytesMut,
    chunk_size: usize,
}

impl ChunkedProcessor {
    pub fn new(chunk_size: usize) -> Self {
        Self {
            buffer: BytesMut::with_capacity(chunk_size * 2),
            chunk_size,
        }
    }

    pub fn push_data(&mut self, data: &[u8]) {
        self.buffer.put_slice(data);
    }

    pub fn process_chunks<F>(&mut self, mut processor: F) -> usize
    where
        F: FnMut(&[u8]),
    {
        let mut processed = 0;

        while self.buffer.len() >= self.chunk_size {
            let chunk = self.buffer.split_to(self.chunk_size);
            processor(&chunk);
            processed += 1;
        }

        processed
    }

    pub fn remaining(&self) -> usize {
        self.buffer.len()
    }

    pub fn flush<F>(&mut self, processor: F)
    where
        F: FnOnce(&[u8]),
    {
        if !self.buffer.is_empty() {
            processor(&self.buffer);
            self.buffer.clear();
        }
    }
}

// Binary serialization
pub trait BinarySerialize {
    fn serialize(&self, buf: &mut BytesMut);
    fn deserialize(buf: &mut impl Buf) -> Result<Self, &'static str>
    where
        Self: Sized;
}

#[derive(Debug, Clone, PartialEq)]
pub struct Point3D {
    pub x: f32,
    pub y: f32,
    pub z: f32,
}

impl BinarySerialize for Point3D {
    fn serialize(&self, buf: &mut BytesMut) {
        buf.put_f32_le(self.x);
        buf.put_f32_le(self.y);
        buf.put_f32_le(self.z);
    }

    fn deserialize(buf: &mut impl Buf) -> Result<Self, &'static str> {
        if buf.remaining() < 12 {
            return Err("Insufficient bytes for Point3D");
        }

        Ok(Self {
            x: buf.get_f32_le(),
            y: buf.get_f32_le(),
            z: buf.get_f32_le(),
        })
    }
}

// Length-prefixed string encoding
pub fn encode_string(s: &str, buf: &mut BytesMut) {
    let bytes = s.as_bytes();
    buf.put_u32_le(bytes.len() as u32);
    buf.put_slice(bytes);
}

pub fn decode_string(buf: &mut impl Buf) -> Result<String, &'static str> {
    if buf.remaining() < 4 {
        return Err("Insufficient bytes for string length");
    }

    let len = buf.get_u32_le() as usize;
    
    if buf.remaining() < len {
        return Err("Insufficient bytes for string data");
    }

    let bytes = buf.copy_to_bytes(len);
    String::from_utf8(bytes.to_vec())
        .map_err(|_| "Invalid UTF-8")
}

// Zero-copy buffer slicing
pub struct BufferReader {
    data: Bytes,
    position: usize,
}

impl BufferReader {
    pub fn new(data: Bytes) -> Self {
        Self { data, position: 0 }
    }

    pub fn read_slice(&mut self, len: usize) -> Option<Bytes> {
        if self.position + len > self.data.len() {
            return None;
        }

        let slice = self.data.slice(self.position..self.position + len);
        self.position += len;
        Some(slice)
    }

    pub fn read_u32_le(&mut self) -> Option<u32> {
        self.read_slice(4).map(|mut slice| slice.get_u32_le())
    }

    pub fn read_u64_le(&mut self) -> Option<u64> {
        self.read_slice(8).map(|mut slice| slice.get_u64_le())
    }

    pub fn remaining(&self) -> usize {
        self.data.len() - self.position
    }

    pub fn reset(&mut self) {
        self.position = 0;
    }
}

// Memory-efficient buffer pool
use std::sync::{Arc, Mutex};

pub struct BufferPool {
    pool: Arc<Mutex<Vec<BytesMut>>>,
    capacity: usize,
    max_size: usize,
}

impl BufferPool {
    pub fn new(capacity: usize, max_size: usize) -> Self {
        Self {
            pool: Arc::new(Mutex::new(Vec::new())),
            capacity,
            max_size,
        }
    }

    pub fn acquire(&self) -> BytesMut {
        let mut pool = self.pool.lock().unwrap();
        pool.pop()
            .unwrap_or_else(|| BytesMut::with_capacity(self.capacity))
    }

    pub fn release(&self, mut buffer: BytesMut) {
        buffer.clear();
        
        let mut pool = self.pool.lock().unwrap();
        if pool.len() < self.max_size {
            pool.push(buffer);
        }
    }
}

// Example usage
fn main() {
    // Message encoding/decoding
    let payload = Bytes::from("Hello, World!");
    let msg = Message::new(1, payload);
    
    let encoded = msg.encode();
    println!("Encoded message size: {} bytes", encoded.len());
    
    let mut buf = encoded.clone();
    let decoded = Message::decode(&mut buf).unwrap();
    println!("Decoded payload: {:?}", String::from_utf8_lossy(&decoded.payload));

    // Chunked processing
    let mut processor = ChunkedProcessor::new(10);
    processor.push_data(b"This is a test message that will be chunked");
    
    let chunks_processed = processor.process_chunks(|chunk| {
        println!("Processing chunk: {:?}", String::from_utf8_lossy(chunk));
    });
    
    println!("Processed {} chunks, {} bytes remaining", 
        chunks_processed, processor.remaining());

    // Binary serialization
    let point = Point3D { x: 1.0, y: 2.0, z: 3.0 };
    let mut buf = BytesMut::new();
    point.serialize(&mut buf);
    
    let mut read_buf = buf.clone();
    let decoded_point = Point3D::deserialize(&mut read_buf).unwrap();
    assert_eq!(point, decoded_point);

    // String encoding
    let mut buf = BytesMut::new();
    encode_string("Hello, Rust!", &mut buf);
    let decoded_str = decode_string(&mut buf).unwrap();
    println!("Decoded string: {}", decoded_str);

    // Zero-copy reading
    let data = Bytes::from(&b"ABCD\x01\x00\x00\x00\x02\x00\x00\x00"[..]);
    let mut reader = BufferReader::new(data);
    
    if let Some(slice) = reader.read_slice(4) {
        println!("Read slice: {:?}", String::from_utf8_lossy(&slice));
    }
    
    if let Some(num1) = reader.read_u32_le() {
        println!("Read u32: {}", num1);
    }

    // Buffer pool
    let pool = BufferPool::new(1024, 10);
    let buf1 = pool.acquire();
    let buf2 = pool.acquire();
    
    pool.release(buf1);
    pool.release(buf2);
}
"""
    }

]