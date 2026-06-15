import { makeScene2D } from "@revideo/2d";
import { Img, Layout, Txt, Video, makeProject } from "@revideo/2d";
import {
  createRef,
  easeInOutCubic,
  interpolate,
  useScene,
  useTime,
  waitFor,
} from "@revideo/core";

interface Caption {
  start: number;
  end: number;
  text: string;
}

interface Variables {
  backgroundVideo?: string;
  captionTrack: Caption[];
  priceOverlay: string;
  regionTag: string;
  language: string;
}

export default makeScene2D(function* (view) {
  const { variables } = useScene();
  const {
    backgroundVideo,
    captionTrack,
    priceOverlay,
    regionTag,
    language,
  } = variables as unknown as Variables;

  const regionRef = createRef<Txt>();
  const priceRef = createRef<Txt>();
  const captionRef = createRef<Txt>();
  const signalBoxRef = createRef<Layout>();

  // 9:16 vertical canvas.
  view.fill("#0a0a0a");

  // Background cooking video (optional).
  if (backgroundVideo) {
    view.add(
      <Video
        src={backgroundVideo}
        width={1080}
        height={1920}
        opacity={0.6}
      />
    );
  } else {
    view.add(
      <Layout
        width={1080}
        height={1920}
        fill="#1a1a2e"
      />
    );
  }

  // Top region tag.
  view.add(
    <Txt
      ref={regionRef}
      text={regionTag}
      fill="#ffffff"
      fontSize={48}
      fontFamily="Noto Sans, sans-serif"
      x={0}
      y={-860}
      opacity={0}
    />
  );

  // Price overlay (the "signal").
  view.add(
    <Layout
      ref={signalBoxRef}
      layout
      direction="column"
      alignItems="center"
      gap={16}
      x={0}
      y={-600}
      opacity={0}
    >
      <Txt
        ref={priceRef}
        text={priceOverlay}
        fill="#ffcc00"
        fontSize={72}
        fontWeight={800}
        fontFamily="Noto Sans, sans-serif"
        textAlign="center"
        shadowColor="#000000"
        shadowBlur={10}
      />
    </Layout>
  );

  // Bottom caption area.
  view.add(
    <Txt
      ref={captionRef}
      text=""
      fill="#ffffff"
      fontSize={56}
      fontFamily="Noto Sans, sans-serif"
      textAlign="center"
      x={0}
      y={760}
      width={960}
      shadowColor="#000000"
      shadowBlur={12}
    />
  );

  // Animate in region tag and price overlay.
  yield* regionRef().opacity(1, 0.5);
  yield* signalBoxRef().opacity(1, 0.5);

  // Animate captions word-by-word-ish (segment by segment).
  if (captionTrack && captionTrack.length > 0) {
    for (const caption of captionTrack) {
      captionRef().text(caption.text);
      const duration = caption.end - caption.start;
      yield* captionRef().opacity(1, 0.2);
      yield* waitFor(Math.max(0.1, duration));
      yield* captionRef().opacity(0, 0.2);
    }
  } else {
    captionRef().text("(no captions provided)");
    yield* waitFor(2);
  }

  // Hold on price overlay at the end.
  yield* waitFor(1);
});

export const project = makeProject({
  scenes: [import("./scene")],
});
