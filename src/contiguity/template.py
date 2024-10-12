from htmlmin import minify


class Template:
    def local(self, file):
        try:
            with open(file, "r") as f:
                file_content = f.read()
                mini = minify(file_content, minify_js=True, minify_css=True)
                return mini
        except IOError:
            raise ValueError("Getting contents from files is not supported in the current environment.")

    async def online(self, file_name):
        # Coming soon
        raise NotImplementedError
