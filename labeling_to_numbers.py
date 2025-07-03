import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import platform

# 한글 폰트 설정
def setup_korean_font():
    """
    운영체제별로 한글 폰트를 설정합니다.
    """
    system = platform.system()
    
    if system == 'Windows':
        plt.rcParams['font.family'] = 'Malgun Gothic'
    elif system == 'Darwin':  # macOS
        plt.rcParams['font.family'] = 'AppleGothic'
    else:  # Linux
        plt.rcParams['font.family'] = 'DejaVu Sans'
    
    plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

# 폰트 설정 실행
setup_korean_font()

def midi_note_to_key_number(note):
    """
    MIDI 음표 문자열(예: 'A0', 'C4')을 0-87 범위의 피아노 건반 번호로 변환합니다.
    A0가 0번, C8이 87번 건반에 해당합니다.
    """
    # 음이름과 옥타브를 분리합니다.
    note_name = note[:-1]
    octave = int(note[-1])
    
    # 각 음이름에 숫자를 매핑합니다.
    note_map = {
        'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 
        'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11
    }
    
    # 표준 MIDI 번호를 계산합니다.
    midi_number = (octave + 1) * 12 + note_map[note_name]
    
    # 88개 건반의 시작인 A0(MIDI 21)를 0으로 맞추기 위해 21을 빼줍니다.
    key_number = midi_number - 21
    
    return key_number

def generate_all_piano_keys():
    """
    88개 피아노 건반의 모든 음표와 라벨을 생성합니다.
    """
    notes = []
    labels = []
    
    # 88개 건반 생성 (A0부터 C8까지)
    octaves = range(0, 9)  # 0옥타브부터 8옥타브까지
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    for octave in octaves:
        for note_name in note_names:
            note = f"{note_name}{octave}"
            try:
                label = midi_note_to_key_number(note)
                if 0 <= label <= 87:  # 88건반 범위 내에서만
                    notes.append(note)
                    labels.append(label)
            except:
                continue
    
    return notes, labels

def create_labeling_dataframe():
    """
    라벨링 데이터를 DataFrame으로 생성하여 시각적으로 확인할 수 있게 합니다.
    """
    notes, labels = generate_all_piano_keys()
    
    df = pd.DataFrame({
        'Note': notes,
        'Label': labels,
        'MIDI_Number': [label + 21 for label in labels],  # 원래 MIDI 번호도 표시
        'Octave': [int(note[-1]) for note in notes],
        'Note_Name': [note[:-1] for note in notes]
    })
    
    return df

def visualize_piano_mapping():
    """
    피아노 건반 매핑을 시각화합니다.
    """
    df = create_labeling_dataframe()
    
    # 흑건과 백건 구분
    black_keys = ['C#', 'D#', 'F#', 'G#', 'A#']
    df['Key_Type'] = df['Note_Name'].apply(lambda x: 'Black' if x in black_keys else 'White')
    
    plt.figure(figsize=(15, 8))
    
    # 서브플롯 1: 전체 건반 분포
    plt.subplot(2, 2, 1)
    colors = ['black' if key_type == 'Black' else 'white' for key_type in df['Key_Type']]
    edge_colors = ['white' if key_type == 'Black' else 'black' for key_type in df['Key_Type']]
    
    plt.scatter(df['Label'], [1]*len(df), c=colors, edgecolors=edge_colors, s=50)
    plt.xlabel('건반 번호 (Label)')
    plt.title('88개 피아노 건반 분포')
    plt.grid(True, alpha=0.3)
    
    # 서브플롯 2: 옥타브별 분포
    plt.subplot(2, 2, 2)
    octave_counts = df['Octave'].value_counts().sort_index()
    plt.bar(octave_counts.index, octave_counts.values)
    plt.xlabel('옥타브')
    plt.ylabel('건반 수')
    plt.title('옥타브별 건반 분포')
    
    # 서브플롯 3: 흑건/백건 분포
    plt.subplot(2, 2, 3)
    key_type_counts = df['Key_Type'].value_counts()
    plt.pie(key_type_counts.values, labels=['흑건', '백건'], autopct='%1.1f%%')
    plt.title('흑건/백건 비율')
    
    # 서브플롯 4: 라벨 연속성 확인
    plt.subplot(2, 2, 4)
    plt.plot(df['Label'], marker='o', markersize=2)
    plt.xlabel('인덱스')
    plt.ylabel('라벨 값')
    plt.title('라벨 연속성 확인')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def validate_labeling():
    """
    라벨링의 정확성을 검증합니다.
    """
    df = create_labeling_dataframe()
    
    print("=== 라벨링 검증 결과 ===")
    print(f"총 건반 수: {len(df)}")
    print(f"라벨 범위: {df['Label'].min()} ~ {df['Label'].max()}")
    print(f"중복 라벨 수: {df['Label'].duplicated().sum()}")
    print(f"누락된 라벨: {set(range(88)) - set(df['Label'])}")
    
    # 중요한 음표들 확인
    important_notes = ['A0', 'C1', 'C4', 'A4', 'C8']
    print("\n=== 주요 음표 라벨링 확인 ===")
    for note in important_notes:
        if note in df['Note'].values:
            label = df[df['Note'] == note]['Label'].iloc[0]
            print(f"{note}: {label}")
    
    return df

def export_labeling_data(df, filename='piano_labeling.csv'):
    """
    라벨링 데이터를 CSV 파일로 내보냅니다.
    """
    df.to_csv(filename, index=False, encoding='utf-8-sig')  # BOM 추가로 한글 깨짐 방지
    print(f"라벨링 데이터가 '{filename}'로 저장되었습니다.")

# 실행 예시
if __name__ == "__main__":
    # 라벨링 데이터 생성 및 검증
    labeling_df = validate_labeling()
    
    # 데이터프레임 출력 (처음 10개와 마지막 10개)
    print("\n=== 라벨링 데이터 샘플 ===")
    print("처음 10개:")
    print(labeling_df.head(10))
    print("\n마지막 10개:")
    print(labeling_df.tail(10))
    
    # 시각화
    visualize_piano_mapping()
    
    # CSV 파일로 저장
    export_labeling_data(labeling_df)
    
    # 모델 학습용 딕셔너리 생성
    note_to_label = dict(zip(labeling_df['Note'], labeling_df['Label']))
    label_to_note = dict(zip(labeling_df['Label'], labeling_df['Note']))
    
    print("\n=== 모델 학습용 매핑 딕셔너리 생성 완료 ===")
    print(f"note_to_label 딕셔너리 크기: {len(note_to_label)}")
    print(f"label_to_note 딕셔너리 크기: {len(label_to_note)}")
