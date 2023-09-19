import pandas as pd

import pyreball as pb

ref = pb.Reference("My Table")
pb.print(f"It is possible to create a link {ref} before the target...")
pb.print_table(pd.DataFrame({"a": [1, 2], "b": [3, 4]}), reference=ref)
pb.print(f"and also link {ref} after the target.")
pb.print(f"It is also possible to create {ref('link with custom text')}.")
