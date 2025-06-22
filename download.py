from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="anvo25/vlms-are-biased",
    repo_type="dataset", 
    local_dir="./dataset",
    local_dir_use_symlinks=False,
    cache_dir="./cache",
)