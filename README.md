# notebooks-pre-commit
A [pre-commit](https://pre-commit.com/) hook for cleaning python notebooks.

### Images downscaling

To downscale your notebooks' images via pre-commit, add the following to your `.pre-commit-config.yaml`:

```yaml
repos:
- repo: https://github.com/sasso-effe/notebooks-pre-commit
  rev: v0.1.0
  hooks:
    - id: downscale-notebook-images
```

You can disable conversion of PNG images to JPEG with:

```yaml
repos:
- repo: https://github.com/sasso-effe/notebooks-pre-commit
  rev: v0.1.0
  hooks:
    - id: downscale-notebook-images
      args: ["--kep-png"]
```

Other options are:

 - `--max-img-res`: Resize images that have one side larger than this number (in pixels). Defaults to 800.
 - `--max-file-size`: Ignore notebooks smaller than this size (in KB). Defaults to 512.