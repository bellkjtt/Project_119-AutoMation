export const convertToWav = async (audioData) => {
  const audioContext = new AudioContext();
  const audioBuffer = await audioContext.decodeAudioData(audioData.buffer);

  const targetSampleRate = 16000;
  const numChannels = audioBuffer.numberOfChannels;
  const length = audioBuffer.length * targetSampleRate / audioBuffer.sampleRate;
  const offlineContext = new OfflineAudioContext(numChannels, length, targetSampleRate);

  const bufferSource = offlineContext.createBufferSource();
  bufferSource.buffer = audioBuffer;

  bufferSource.connect(offlineContext.destination);
  bufferSource.start(0);

  const resampledBuffer = await offlineContext.startRendering();
  return encodeWAV(resampledBuffer);
};

const encodeWAV = (audioBuffer) => {
  const numChannels = audioBuffer.numberOfChannels;
  const sampleRate = audioBuffer.sampleRate;
  const format = 1; // PCM
  const bitDepth = 16;
  const bytesPerSample = bitDepth / 8;

  let buffers = [];
  for (let i = 0; i < numChannels; i++) {
    buffers.push(audioBuffer.getChannelData(i));
  }

  const interleaved = interleave(buffers);
  const buffer = new ArrayBuffer(44 + interleaved.length * bytesPerSample);
  const view = new DataView(buffer);

  writeString(view, 0, 'RIFF');
  view.setUint32(4, 36 + interleaved.length * bytesPerSample, true);
  writeString(view, 8, 'WAVE');
  writeString(view, 12, 'fmt ');
  view.setUint32(16, 16, true);
  view.setUint16(20, format, true);
  view.setUint16(22, numChannels, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * numChannels * bytesPerSample, true);
  view.setUint16(32, numChannels * bytesPerSample, true);
  view.setUint16(34, bitDepth, true);
  writeString(view, 36, 'data');
  view.setUint32(40, interleaved.length * bytesPerSample, true);

  floatTo16BitPCM(view, 44, interleaved);

  return buffer;
};

const writeString = (view, offset, string) => {
  for (let i = 0; i < string.length; i++) {
    view.setUint8(offset + i, string.charCodeAt(i));
  }
};

const interleave = (buffers) => {
  const length = buffers[0].length;
  const result = new Float32Array(length * buffers.length);

  let inputIndex = 0;
  for (let i = 0; i < length; i++) {
    for (let j = 0; j < buffers.length; j++) {
      result[inputIndex++] = buffers[j][i];
    }
  }
  return result;
};

const floatTo16BitPCM = (output, offset, input) => {
  for (let i = 0; i < input.length; i++, offset += 2) {
    const s = Math.max(-1, Math.min(1, input[i]));
    output.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
  }
};