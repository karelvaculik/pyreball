def define_env(env):
    @env.macro
    def inline_source(reference):
        print("Reading reference:")
        with open(reference, "r") as f:
            file_content = f.read()
        return f"```py\n{file_content}\n```"
