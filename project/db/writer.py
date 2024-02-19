from contextlib import suppress

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine


async def write_db_texts(engine: AsyncEngine) -> None:
    """
    Write texts to the database.
    :param engine: AsyncEngine
    """
    with suppress(IntegrityError):
        async with engine.begin() as connection:
            await connection.execute(text(texts_data))


texts_data = """
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

INSERT INTO `text_buttons` (`id`, `code`, `text`) VALUES
(1, 'BACK', '‹ Back'),
(2, 'MAIN', '🏠 Main'),
(3, 'ISSUES_LIST', '🗂 List of Bounties'),
(4, 'ISSUE_INFO', '🔗 Open Bounty'),
(5, 'CREATE_BOUNTY', '🪄 Create Your Own Bounty'),
(6, 'ISSUE_CREATED', '✏️ Leave Your Comment'),
(7, 'ISSUE_CLOSING', '✏️ Leave Your Comment'),
(8, 'ISSUE_APPROVED', '✏️ Leave Your Comment'),
(9, 'ISSUE_COMPLETED', '✏️ Leave Your Comment'),
(10, 'SUBSCRIBE_NOTIFICATION', '🔔 Subscribe To Notifications'),
(11, 'UNSUBSCRIBE_NOTIFICATION', '🔕 Unsubscribe From Notifications'),
(12, 'TOP_CONTRIBUTORS', '🏆 Top Contributors'),
(13, 'HALL_OF_FAME', '🏛️ Hall of Fame');

INSERT INTO `text_messages` (`id`, `code`, `text`, `preview_url`) VALUES
(1, 'UNKNOWN_ERROR', '<p><strong>An unexpected error occurred!</strong></p>\r\n<p>The report has been sent to the developers.</p>', 'https://telegra.ph//file/dccd34b9ae04c57f022db.jpg'),
(2, 'MAIN_MENU', '<p><strong>TON Foundation actively supports teams and projects that enrich TON Ecosystem</strong>, whether by improving its core infrastructure, introducing innovative use cases, or making it more developer-friendly.</p>\r\n<blockquote>\r\n<p>Available support initiatives are of two kinds -&nbsp;<strong>Grants</strong>&nbsp;and&nbsp;<strong>Bounties</strong>. The&nbsp;<strong>Grants program</strong>&nbsp;is focused on providing milestone based financial support to teams and projects building comprehensive, full-fledged products, while the&nbsp;<strong>Bounties program</strong>&nbsp;serves as a community driven improvement suggestions and offers quick financial rewards for individual tasks such as contributions to development tools, educational content, and community resources.</p>\r\n</blockquote>', 'https://github.com/ton-society/grants-and-bounties/raw/main/assets/cover.png'),
(3, 'ISSUES_LIST', '<p><strong>List of Bounties:</strong></p>', 'https://telegra.ph//file/39c7504768ee0168a5118.jpg'),
(4, 'ISSUE_INFO', '<p>{title}</p>\r\n<p>{labels}</p>\r\n<p>{summary}</p>\r\n<p>{rewards}</p>\r\n<p>{creator}</p>\r\n<p>{assignees}</p>', 'https://telegra.ph//file/e941348bbe37d0ced1e6f.jpg'),
(5, 'WEEKLY_DIGEST', '<p>📊 <strong>Weekly Update Digest!</strong></p>\r\n<p>🔍 Active bounties: <strong>{num_active}<br></strong>✅ Approved bounties: <strong>{num_approved_assignee}</strong><br>🔄 Bounties seeking suggestions: <strong>{num_suggested_opinions}</strong></p>\r\n<p>📣 We value your feedback! Join the community discussion and participate in shaping the future. Click the "Create Your Own Bounty" button to get started.</p>\r\n<p><strong>Happy contributing!</strong></p>', 'https://telegra.ph//file/fd6981d63b4b03c501c44.jpg'),
(6, 'ISSUE_CREATED', '<p>{title}</p>\r\n<p>{labels}</p>\r\n<p>{summary}</p>\r\n<p>{rewards}</p>', 'https://telegra.ph//file/f40e628291df5d24aca69.jpg'),
(7, 'ISSUE_CLOSING', '<p>{title}</p>\r\n<p>{labels}</p>\r\n<p>{summary}</p>', 'https://telegra.ph//file/ea1f2ef5d8dbe5ecc222b.jpg'),
(8, 'ISSUE_APPROVED', '<p>{title}</p>\r\n<p>{labels}</p>\r\n<p>{summary}</p>\r\n<p>{rewards}</p>', 'https://telegra.ph//file/d5072ef1dee916c1ef7df.jpg'),
(9, 'ISSUE_COMPLETED', '<p>{title}</p>\r\n<p>{labels}</p>\r\n<p>{summary}</p>\r\n<p>{assignees}</p>', 'https://telegra.ph//file/f5c2c0f91c6f7f0c532c7.jpg'),
(10, 'TOP_CONTRIBUTORS', '<p><strong>🏆 TOP Contributors!<br><br></strong>{top_contributors}</p>', 'https://telegra.ph//file/25f1bb1c0d8abb1a33af4.jpg');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
"""
