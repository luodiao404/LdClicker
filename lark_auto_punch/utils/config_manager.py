"""
配置导入导出工具
"""
import json
import zipfile
from datetime import datetime
from pathlib import Path


class ConfigManager:
    """配置导入导出管理器"""

    @staticmethod
    def export_config(images_dir, image_names, output_path):
        """
        导出配置到 zip 文件
        :param images_dir: 图片目录
        :param image_names: 图片名称列表
        :param output_path: 输出文件路径
        :return: (success, message)
        """
        images_dir = Path(images_dir)

        # 检查已配置的图片
        configured_images = [
            name for name in image_names
            if (images_dir / f"{name}.png").exists()
        ]

        if not configured_images:
            return False, "没有已配置的图片可以导出！"

        try:
            # 创建配置信息
            config_info = {
                "export_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "images": configured_images,
                "version": "1.0"
            }

            # 创建 zip 文件
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 写入配置信息
                zipf.writestr("config.json", json.dumps(config_info, indent=2, ensure_ascii=False))

                # 打包所有图片
                for name in configured_images:
                    img_path = images_dir / f"{name}.png"
                    zipf.write(img_path, f"images/{name}.png")

            return True, f"成功导出 {len(configured_images)} 张图片"

        except Exception as e:
            return False, f"导出失败: {str(e)}"

    @staticmethod
    def import_config(zip_path, images_dir, image_names):
        """
        从 zip 文件导入配置
        :param zip_path: zip 文件路径
        :param images_dir: 图片目录
        :param image_names: 图片名称列表
        :return: (success, message, imported_count)
        """
        import shutil

        images_dir = Path(images_dir)
        imported_count = 0

        try:
            # 解压 zip 文件
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                # 读取配置信息
                if "config.json" in zipf.namelist():
                    config_data = json.loads(zipf.read("config.json").decode('utf-8'))
                    images_list = config_data.get("images", [])
                else:
                    # 兼容旧版本，直接读取所有图片
                    images_list = image_names

                # 解压图片
                for name in images_list:
                    img_file = f"images/{name}.png"
                    if img_file in zipf.namelist():
                        # 解压到临时位置
                        zipf.extract(img_file, images_dir.parent)

                        # 移动到正确位置
                        src = images_dir.parent / "images" / f"{name}.png"
                        dst = images_dir / f"{name}.png"

                        if src.exists():
                            shutil.move(str(src), str(dst))
                            imported_count += 1

                # 清理临时目录
                temp_dir = images_dir.parent / "images"
                if temp_dir.exists() and temp_dir != images_dir:
                    shutil.rmtree(temp_dir)

            return True, f"成功导入 {imported_count} 张图片", imported_count

        except Exception as e:
            return False, f"导入失败: {str(e)}", 0
