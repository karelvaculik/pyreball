def define_env(env):
    @env.macro
    def inline_source(reference, language: str = "python"):
        print("Reading reference:")
        with open(reference, "r") as f:
            file_content = f.read()
        return f"```{language}\n{file_content}\n```"
