import zipfile
import io

def unzipped(input_zip):
    input_zip = zipfile.ZipFile(io.BytesIO(input_zip))
    return {name: input_zip.read(name) for name in input_zip.namelist()}

def zipped(input_clear, filename):
    buff = io.BytesIO()
    zip_archive = zipfile.ZipFile(buff, mode="w", compression=zipfile.ZIP_DEFLATED)
    zip_archive.writestr(filename, input_clear)
    zip_archive.close()
    return buff.getvalue()
