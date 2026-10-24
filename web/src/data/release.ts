import release from './release.json';

export const { version, brand } = release;
export const installer = release.gpuInstaller || `${brand}-Setup-${version}.exe`;
export const releaseUrl = `https://github.com/bryramirezp/vox0/releases/tag/v${version}`;
export const downloadUrl = `https://github.com/bryramirezp/vox0/releases/download/v${version}/${installer}`;
export const hashesUrl = `https://github.com/bryramirezp/vox0/releases/download/v${version}/SHA256SUMS.txt`;
