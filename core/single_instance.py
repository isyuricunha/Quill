"""
Single Instance Lock

Checks whether another Bragi instance is already running.
"""

import os
import sys
import logging

from core.app_paths import get_user_data_dir


logger = logging.getLogger(__name__)


class SingleInstanceLock:
    """Single-instance lock manager."""

    def __init__(self, lock_file_name="bragi.lock"):
        """Initialize the lock inside Bragi's active user-data directory."""
        data_dir = get_user_data_dir()
        data_dir.mkdir(parents=True, exist_ok=True)

        self.lock_file_path = data_dir / lock_file_name
        self.lock_file = None

    def acquire(self) -> bool:
        """Try to acquire the process lock."""
        try:
            if sys.platform == "win32":
                import msvcrt

                self.lock_file = open(self.lock_file_path, "w")
                try:
                    msvcrt.locking(self.lock_file.fileno(), msvcrt.LK_NBLCK, 1)
                except IOError:
                    self.lock_file.close()
                    self.lock_file = None
                    logger.warning("Another instance of Bragi is already running")
                    return False
            else:
                import fcntl

                self.lock_file = open(self.lock_file_path, "w")
                try:
                    fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                except IOError:
                    self.lock_file.close()
                    self.lock_file = None
                    logger.warning("Another instance of Bragi is already running")
                    return False

            self.lock_file.write(str(os.getpid()))
            self.lock_file.flush()
            logger.info("Single instance lock acquired")
            return True

        except Exception as e:
            logger.error(f"Error acquiring lock: {e}")
            return False

    def release(self):
        """Release the lock."""
        if self.lock_file:
            try:
                if sys.platform == "win32":
                    import msvcrt
                    msvcrt.locking(self.lock_file.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)

                self.lock_file.close()
                self.lock_file = None

                if self.lock_file_path.exists():
                    self.lock_file_path.unlink()

                logger.info("Single instance lock released")
            except Exception as e:
                logger.error(f"Error releasing lock: {e}")

    def __enter__(self):
        if not self.acquire():
            raise RuntimeError("Another instance of Bragi is already running")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    print("\n=== Testing SingleInstanceLock ===\n")
    lock = SingleInstanceLock()

    if lock.acquire():
        print("[OK] Lock acquired successfully!")
        print(f"Lock file: {lock.lock_file_path}")
        print("\nTry running this script in another terminal to test.")
        print("Press Enter to release lock...")
        input()
        lock.release()
        print("[OK] Lock released")
    else:
        print("[ERROR] Another instance is already running!")
