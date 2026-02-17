---
sidebar_position: 2
title: Voice-to-Action Pipelines
description: Building end-to-end speech-to-robot-action systems
keywords: [voice, speech, whisper, asr, voice-control]
---

# Voice-to-Action Pipelines

## Introduction

Voice-to-action pipelines enable hands-free robot control by converting speech to executable robot commands. This chapter covers speech recognition, natural language understanding, and action execution.

## Pipeline Architecture

```
Microphone → Speech Recognition → NLU → Action Planning → Robot Execution
    ↓              ↓                 ↓          ↓              ↓
  Audio         "Pick up"        Intent    [grasp,        Execute
  Stream         Text            Parsing    move]         Motion
```

## Speech Recognition with Whisper

### OpenAI Whisper Integration

```python
import rclpy
from rclpy.node import Node
from audio_common_msgs.msg import AudioData
from std_msgs.msg import String
import whisper
import numpy as np
import io
import wave

class WhisperASR(Node):
    def __init__(self):
        super().__init__('whisper_asr')

        # Load Whisper model
        self.model = whisper.load_model("base")  # or "small", "medium", "large"

        # Subscribe to audio stream
        self.audio_sub = self.create_subscription(
            AudioData,
            '/audio/audio',
            self.audio_callback,
            10
        )

        # Publish transcribed text
        self.text_pub = self.create_publisher(
            String,
            '/voice_command',
            10
        )

        # Audio buffer
        self.audio_buffer = []
        self.sample_rate = 16000
        self.buffer_duration = 3.0  # seconds

    def audio_callback(self, msg):
        # Accumulate audio data
        self.audio_buffer.extend(msg.data)

        # Process when buffer is full
        buffer_size = int(self.sample_rate * self.buffer_duration)
        if len(self.audio_buffer) >= buffer_size:
            self.process_audio()
            self.audio_buffer = []

    def process_audio(self):
        # Convert to numpy array
        audio_np = np.array(self.audio_buffer, dtype=np.float32)
        audio_np = audio_np / 32768.0  # Normalize

        # Transcribe with Whisper
        result = self.model.transcribe(
            audio_np,
            language='en',
            task='transcribe'
        )

        text = result['text'].strip()

        if text:
            self.get_logger().info(f'Transcribed: {text}')
            self.text_pub.publish(String(data=text))
```

### Real-Time Streaming ASR

```python
import pyaudio
import threading

class StreamingASR(Node):
    def __init__(self):
        super().__init__('streaming_asr')

        # Audio configuration
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000

        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK,
            stream_callback=self.audio_callback
        )

        # Whisper model
        self.model = whisper.load_model("base")

        # Publisher
        self.text_pub = self.create_publisher(String, '/voice_command', 10)

        # Start streaming
        self.stream.start_stream()

    def audio_callback(self, in_data, frame_count, time_info, status):
        # Process audio in separate thread
        threading.Thread(
            target=self.process_chunk,
            args=(in_data,)
        ).start()

        return (in_data, pyaudio.paContinue)

    def process_chunk(self, audio_data):
        # Convert to numpy
        audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
        audio_np = audio_np / 32768.0

        # Transcribe
        result = self.model.transcribe(audio_np)
        text = result['text'].strip()

        if text:
            self.text_pub.publish(String(data=text))
```

## Wake Word Detection

### Porcupine Wake Word

```python
import pvporcupine

class WakeWordDetector(Node):
    def __init__(self):
        super().__init__('wake_word_detector')

        # Initialize Porcupine
        self.porcupine = pvporcupine.create(
            access_key='YOUR_ACCESS_KEY',
            keywords=['jarvis', 'computer']  # Wake words
        )

        # Audio stream
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length
        )

        # State
        self.listening = False

        # Start detection
        self.timer = self.create_timer(0.01, self.detect_wake_word)

    def detect_wake_word(self):
        pcm = self.stream.read(self.porcupine.frame_length)
        pcm = np.frombuffer(pcm, dtype=np.int16)

        keyword_index = self.porcupine.process(pcm)

        if keyword_index >= 0:
            self.get_logger().info('Wake word detected!')
            self.listening = True
            self.start_listening()

    def start_listening(self):
        # Activate ASR for command
        self.get_logger().info('Listening for command...')
        # Trigger ASR node
```

## Natural Language Understanding

### Intent Classification

```python
from openai import OpenAI

class IntentClassifier(Node):
    def __init__(self):
        super().__init__('intent_classifier')

        self.client = OpenAI()

        # Subscribe to transcribed text
        self.text_sub = self.create_subscription(
            String,
            '/voice_command',
            self.text_callback,
            10
        )

        # Publish structured intent
        self.intent_pub = self.create_publisher(
            String,
            '/robot_intent',
            10
        )

    def text_callback(self, msg):
        text = msg.data

        # Classify intent
        intent = self.classify_intent(text)

        # Publish intent
        self.intent_pub.publish(String(data=intent))

    def classify_intent(self, text):
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """Classify robot commands into intents.
                    Return JSON: {"intent": "...", "entities": {...}}

                    Intents: navigate, grasp, release, look, follow, stop
                    """
                },
                {"role": "user", "content": text}
            ],
            temperature=0.1
        )

        return response.choices[0].message.content
```

## Action Execution

### Voice Command Executor

```python
import json
from geometry_msgs.msg import Twist, Pose

class VoiceCommandExecutor(Node):
    def __init__(self):
        super().__init__('voice_command_executor')

        # Subscribe to intents
        self.intent_sub = self.create_subscription(
            String,
            '/robot_intent',
            self.intent_callback,
            10
        )

        # Publishers for robot control
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.goal_pub = self.create_publisher(Pose, '/goal_pose', 10)
        self.gripper_pub = self.create_publisher(String, '/gripper_command', 10)

    def intent_callback(self, msg):
        try:
            intent_data = json.loads(msg.data)
            intent = intent_data['intent']
            entities = intent_data.get('entities', {})

            self.execute_intent(intent, entities)

        except json.JSONDecodeError:
            self.get_logger().error('Failed to parse intent')

    def execute_intent(self, intent, entities):
        if intent == 'navigate':
            self.navigate(entities)
        elif intent == 'grasp':
            self.grasp(entities)
        elif intent == 'release':
            self.release()
        elif intent == 'stop':
            self.stop()
        elif intent == 'follow':
            self.follow(entities)

    def navigate(self, entities):
        location = entities.get('location', 'unknown')
        self.get_logger().info(f'Navigating to {location}')

        # Publish navigation goal
        goal = Pose()
        # Set goal based on location
        self.goal_pub.publish(goal)

    def grasp(self, entities):
        object_name = entities.get('object', 'unknown')
        self.get_logger().info(f'Grasping {object_name}')

        # Close gripper
        self.gripper_pub.publish(String(data='close'))

    def stop(self):
        self.get_logger().info('Stopping robot')

        # Publish zero velocity
        cmd = Twist()
        self.cmd_vel_pub.publish(cmd)
```

## Multimodal Feedback

### Voice Response System

```python
from gtts import gTTS
import pygame
import tempfile

class VoiceResponseSystem(Node):
    def __init__(self):
        super().__init__('voice_response')

        # Initialize pygame for audio playback
        pygame.mixer.init()

        # Subscribe to robot status
        self.status_sub = self.create_subscription(
            String,
            '/robot_status',
            self.status_callback,
            10
        )

    def status_callback(self, msg):
        status = msg.data

        # Generate appropriate response
        response = self.generate_response(status)

        # Speak response
        self.speak(response)

    def generate_response(self, status):
        responses = {
            'task_complete': 'Task completed successfully',
            'obstacle_detected': 'Obstacle detected, finding alternate path',
            'battery_low': 'Battery is low, returning to charging station',
            'error': 'An error occurred, please assist'
        }

        return responses.get(status, 'Status update received')

    def speak(self, text):
        # Generate speech with gTTS
        tts = gTTS(text=text, lang='en')

        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts.save(fp.name)
            temp_file = fp.name

        # Play audio
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()

        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
```

## Complete Voice-to-Action System

### Integrated Pipeline

```python
class VoiceToActionPipeline(Node):
    def __init__(self):
        super().__init__('voice_to_action_pipeline')

        # Components
        self.wake_word_detector = WakeWordDetector()
        self.asr = WhisperASR()
        self.intent_classifier = IntentClassifier()
        self.executor = VoiceCommandExecutor()
        self.voice_response = VoiceResponseSystem()

        # State machine
        self.state = 'idle'  # idle, listening, processing, executing

    def run(self):
        while rclpy.ok():
            if self.state == 'idle':
                # Wait for wake word
                pass
            elif self.state == 'listening':
                # Capture audio and transcribe
                pass
            elif self.state == 'processing':
                # Classify intent and plan action
                pass
            elif self.state == 'executing':
                # Execute robot action
                pass

            rclpy.spin_once(self, timeout_sec=0.1)
```

## Performance Optimization

### Latency Reduction

```python
class OptimizedVoiceControl(Node):
    def __init__(self):
        super().__init__('optimized_voice_control')

        # Use smaller Whisper model for speed
        self.model = whisper.load_model("tiny")  # Fastest

        # Cache common commands
        self.command_cache = {}

        # Parallel processing
        self.executor = ThreadPoolExecutor(max_workers=4)

    def process_audio_async(self, audio_data):
        # Process in thread pool
        future = self.executor.submit(self.transcribe, audio_data)
        future.add_done_callback(self.handle_transcription)

    def transcribe(self, audio_data):
        # Check cache first
        audio_hash = hash(audio_data.tobytes())
        if audio_hash in self.command_cache:
            return self.command_cache[audio_hash]

        # Transcribe
        result = self.model.transcribe(audio_data)
        text = result['text']

        # Cache result
        self.command_cache[audio_hash] = text

        return text
```

## Best Practices

1. **Use wake words** - Avoid continuous listening for privacy and efficiency
2. **Provide audio feedback** - Confirm commands with voice responses
3. **Handle noise** - Implement noise cancellation and filtering
4. **Support multiple languages** - Use Whisper's multilingual capabilities
5. **Implement timeouts** - Handle silence and unclear commands
6. **Test in real environments** - Validate with background noise

## Common Issues

- High latency affecting user experience
- Poor recognition in noisy environments
- Ambiguous commands requiring clarification
- Privacy concerns with continuous audio recording
- Resource usage from large ASR models

## Next Steps

Learn how to implement cognitive planning for complex, multi-step tasks.
