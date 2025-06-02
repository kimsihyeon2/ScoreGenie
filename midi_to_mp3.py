import subprocess
import sys
import os

def midi_to_mp3(
    midi_path: str,
    soundfont_path: str,
    output_mp3_path: str,
    sample_rate: int = 44100,
    vbr_qscale: int = 2,
    keep_wav: bool = False
):
    """
    MIDI 파일을 FluidSynth로 WAV로 렌더링한 뒤, FFmpeg로 MP3로 인코딩하는 함수.

    :param midi_path: 변환할 MIDI 파일 전체 경로 (예: "D:\\songs\\example.mid")
    :param soundfont_path: 사용할 SoundFont 파일 전체 경로 (예: "D:\\SoundFonts\\FluidR3_GM.sf2")
    :param output_mp3_path: 최종 생성될 MP3 파일 전체 경로 (예: "D:\\songs\\example.mp3")
    :param sample_rate: FluidSynth로 렌더링할 때 사용할 샘플레이트 (기본 44100)
    :param vbr_qscale: FFmpeg로 MP3 인코딩 시 사용할 VBR 품질 값 (0~9, 작을수록 고음질. 기본 2)
    :param keep_wav: 중간에 생성된 WAV 파일을 남길지 여부 (기본 False → 생성 후 삭제)
    """

    # 1) 입력 경로·출력 경로 유효성 검사
    if not os.path.isfile(midi_path):
        raise FileNotFoundError(f"MIDI 파일을 찾을 수 없습니다: {midi_path}")
    if not os.path.isfile(soundfont_path):
        raise FileNotFoundError(f"SoundFont 파일을 찾을 수 없습니다: {soundfont_path}")

    # mp3 파일이 생성될 폴더가 없다면, 디렉터리 생성
    mp3_dir = os.path.dirname(output_mp3_path)
    if mp3_dir and not os.path.isdir(mp3_dir):
        os.makedirs(mp3_dir, exist_ok=True)

    # 중간 WAV 파일 경로를 설정 (MP3와 같은 디렉터리에, 같은 이름의 .wav)
    base_name = os.path.splitext(os.path.basename(midi_path))[0]
    wav_path = os.path.join(mp3_dir, base_name + ".wav")

    # 2)  FluidSynth 호출: MIDI → WAV
    fluidsynth_cmd = [
        "fluidsynth",
        "-ni",                      # 대화형 모드 없이 렌더링
        "-F", wav_path,             # 출력 WAV 파일 경로
        "-r", str(sample_rate),     # 샘플레이트
        soundfont_path,             # SoundFont(.sf2) 경로
        midi_path                    # MIDI 파일 경로
    ]
    print("▶ FluidSynth 명령 실행:", " ".join(fluidsynth_cmd))
    try:
        subprocess.run(fluidsynth_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print("Error: FluidSynth 실행 중 오류가 발생했습니다.")
        print(e.stderr.decode("utf-8", errors="ignore"))
        raise

    # 생성된 WAV 파일이 정상적으로 만들어졌는지 확인
    if not os.path.isfile(wav_path):
        raise FileNotFoundError(f"WAV 파일 생성에 실패했습니다. 예상 경로: {wav_path}")
    print(f"✓ WAV 파일 생성 완료: {wav_path}")

    # 3)  FFmpeg 호출: WAV → MP3
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",                        # 기존 파일 덮어쓰기
        "-i", wav_path,              # 입력 WAV 파일
        "-codec:a", "libmp3lame",    # LAME MP3 인코더 사용
        "-qscale:a", str(vbr_qscale),# VBR 품질 설정
        output_mp3_path              # 출력 MP3 파일 경로
    ]
    print("▶ FFmpeg 명령 실행:", " ".join(ffmpeg_cmd))
    try:
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print("Error: FFmpeg 실행 중 오류가 발생했습니다.")
        print(e.stderr.decode("utf-8", errors="ignore"))
        raise

    # mp3 파일이 정상 생성되었는지 확인
    if not os.path.isfile(output_mp3_path):
        raise FileNotFoundError(f"MP3 파일 생성에 실패했습니다. 예상 경로: {output_mp3_path}")
    print(f"✓ MP3 파일 생성 완료: {output_mp3_path}")

    # 4) 중간 WAV 파일 삭제 여부 결정
    if not keep_wav:
        try:
            os.remove(wav_path)
            print(f"✓ 중간 WAV 파일 삭제 완료: {wav_path}")
        except Exception as e:
            print(f"⚠️ 중간 WAV 파일 삭제 중 오류: {e}")

    return output_mp3_path


if __name__ == "__main__":
    # 예시: 커맨드라인 인수로 MIDI 경로를 받아 변환하려면 다음과 같이 사용합니다.
    # python midi_to_mp3.py "D:\songs\example.mid"
    #
    # SoundFont 경로와 출력 폴더는 이 스크립트 내에서 하드코딩하거나,
    # 추가로 sys.argv를 읽어서 동적으로 처리할 수도 있습니다.

    if len(sys.argv) < 2:
        print("사용법: python midi_to_mp3.py <MIDI 파일 전체 경로>")
        sys.exit(1)

    midi_file = sys.argv[1]
    # 필요하다면 명령행 인수로 SoundFont 경로도 받도록 수정할 수 있습니다.
    soundfont_file = r"D:\SoundFonts\FluidR3_GM.sf2"

    # 결과 MP3 파일을 저장할 경로 (MIDI와 동일한 폴더, 확장자만 .mp3로 바꿈)
    base_name = os.path.splitext(os.path.basename(midi_file))[0]
    output_folder = os.path.dirname(midi_file)
    output_mp3 = os.path.join(output_folder, base_name + ".mp3")

    try:
        result = midi_to_mp3(
            midi_path=midi_file,
            soundfont_path=soundfont_file,
            output_mp3_path=output_mp3,
            sample_rate=44100,
            vbr_qscale=2,
            keep_wav=False    # True로 하면 WAV를 삭제하지 않습니다.
        )
        print(f"\n=== 변환 성공: {result} ===")
    except Exception as ex:
        print(f"\n!!! 변환 중 오류 발생: {ex}")
        sys.exit(1)
