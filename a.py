from data_io.file_io import data_from_jsonl

src_path = "./in/gofuzz_rst.jsonl"
dst_path = "./out/gofuzz_rst.jsonl"


for line in data_from_jsonl(src_path):
    print(line)

