import pyreball as pb

json_str = '{\n  "a": 12,\n  "b": [2, 3, 4]\n}'

pb.print(pb.code_block(json_str, syntax_highlight="json"))
