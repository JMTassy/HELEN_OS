def verify_artifact(artifact: dict) -> bool:
    if "artifact_id" not in artifact:
        return False
    if "content_hash" not in artifact:
        return False
    if "type" not in artifact:
        return False
    return True


def verify_artifacts(artifacts: list[dict]) -> bool:
    if not artifacts:
        return False
    return all(verify_artifact(a) for a in artifacts)
