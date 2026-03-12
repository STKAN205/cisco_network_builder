from pathlib import Path


def export_configs(configs, output_dir, base_name):
    if not configs:
        raise ValueError("Chưa có config để xuất file.")

    if not base_name:
        raise ValueError("Tên file không được để trống.")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for router_name, config_text in configs.items():
        output_path = output_dir / f"{base_name}_{router_name}.txt"
        output_path.write_text(config_text, encoding="utf-8")
